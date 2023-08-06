from frasco import Feature, action, AttrDict, current_app, signal, command, request, current_context, json, Response
from elasticsearch import Elasticsearch
import math


class SearchFeature(Feature):
    name = "search"
    defaults = {"hosts": [{"host": "localhost"}],
                "pagination_per_page": 10,
                "index_models": {},
                "autocomplete": {},
                "autocomplete_url": "/_autocomplete/<doc_type>/<field>",
                "autocomplete_endpoint": "autocomplete",
                "indexes": {},
                "use_only_one_index": False,
                "default_index": "frasco",
                "create_indexes": True,
                "indexes_settings": {},
                "mapping": {},
                "use_redis_partial_models": False}

    def init_app(self, app):
        self.es = Elasticsearch(self.options["hosts"])
        if self.options["index_models"]:
            signal("model_saved").connect(self._index_model_on_change)
            signal("model_deleted").connect(self._delete_model_on_change)
        if self.options["create_indexes"]:
            self.create_all()
        if self.options["autocomplete_url"]:
            app.add_url_rule(self.options["autocomplete_url"], self.options["autocomplete_endpoint"],
                self.autocomplete_endpoint)

    def get_index(self, doc_type, index=None):
        if index:
            return index
        if self.options["use_only_one_index"]:
            return self.options["default_index"]

        indexes = set()
        for dt in doc_type.split(","):
            given = False
            for index, doc_types in self.options["indexes"].iteritems():
                if dt.strip() in doc_types:
                    indexes.add(index)
                    given = True
                    break
            if not given:
                indexes.add(doc_type.lower())
        return ",".join(indexes)

    @command()
    def create_all(self):
        indexes = set(self.options["indexes"].keys())
        for model in self.options["index_models"]:
            indexes.add(self.get_index(model))

        mappings = self.options["mapping"]
        for doc_type in self.options["autocomplete"]:
            if doc_type not in mappings:
                mappings[doc_type] = {}
            indexes.add(self.get_index(doc_type))

        for index in indexes:
            self.create_index(index, self.options["indexes_settings"].get(index, {}), 400)
        for doc_type, doc_mapping in mappings.iteritems():
            self.create_mapping(doc_type.lower(), doc_mapping, ignore_conflicts=True)

    @command()
    def delete_all(self):
        for index in self.options["indexes"]:
            self.delete_index(index)
        for doc_type in self.options["mapping"]:
            self.delete_index(self.get_index(doc_type))

    @command()
    @action("create_search_index", default_option="name")
    def create_index(self, name, settings=None, ignore=None):
        self.es.indices.create(index=name,
            body={"settings": settings or {}}, ignore=ignore)

    @command()
    @action("delete_search_index", default_option="name")
    def delete_index(self, name):
        self.es.indices.delete(index=name)

    @command()
    @action("create_search_mapping")
    def create_mapping(self, name, mapping, index=None, with_autocomplete=True, ignore_conflicts=False):
        if name in self.options["autocomplete"]:
            mapping.setdefault("properties", {})
            for prop in self.options["autocomplete"][name]:
                if isinstance(prop, list):
                    prop = prop[0]
                mapping["properties"]["suggest_%s" % prop] = {
                    "type": "completion",
                    "index_analyzer": "simple",
                    "search_analyzer": "simple",
                    "payloads": True}

        self.es.indices.put_mapping(index=self.get_index(name, index),
            doc_type=name, body=dict([(name, mapping)]), ignore_conflicts=ignore_conflicts)

    @command()
    def reindex_models(self, models=None):
        if models:
            models = models.split(",")
        else:
            models = self.options["index_models"].keys()
        for name in models:
            command.echo("Indexing %s..." % name)
            for obj in current_app.features.models.query(name).all():
                self.index_model(obj)

    @action("index_doc_for_search")
    def index(self, doc_type, id, doc, index=None, refresh=True, **kwargs):
        doc = dict(doc)

        if doc_type in self.options["autocomplete"]:
            for props in self.options["autocomplete"][doc_type]:
                if isinstance(props, list):
                    props = [props]
                input = [doc[k] for k in props]
                output = doc[props[0]]
                payload = {"id": id}
                doc["suggest_%s" % props[0]] = {"input": input,
                    "output": output, "payload": payload}

        index = self.get_index(doc_type, index)
        current_app.logger.debug("Indexing document %s in %s/%s" % (id, index, doc_type))
        return self.es.index(index=index, doc_type=doc_type, id=id, body=doc, refresh=refresh, **kwargs)

    @action("index_model_for_search", default_option="obj")
    def index_model(self, obj, fields=None, extra_doc=None, **kwargs):
        model = obj.__class__.__name__
        doc_type = model.lower()
        doc = obj.for_json()
        if not fields and model in self.options["index_models"]:
            fields = self.options["index_models"][model]
        if fields:
            doc = dict((k, doc[k]) for k in fields)
        if extra_doc:
            doc.update(extra_doc)
        return self.index(doc_type, str(obj.id), doc, **kwargs)

    def _index_model_on_change(self, backend, obj):
        for name, fields in self.options["index_models"].iteritems():
            if obj.__class__.__name__ == name:
                return self.index_model(obj)

    @action("delete_search_doc")
    def delete(self, doc_type, id, index=None, **kwargs):
        index = self.get_index(doc_type, index)
        current_app.logger.debug("Deindexing document %s in %s/%s" % (id, index, doc_type))
        return self.es.delete(index=index, doc_type=doc_type, id=id, **kwargs)

    @action("delete_search_model", default_option="obj")
    def delete_model(self, obj, **kwargs):
        return self.delete(obj.__class__.__name__.lower(), obj.id, **kwargs)

    def _delete_model_on_change(self, backend, obj):
        for name, fields in self.options["index_models"].iteritems():
            if obj.__class__.__name__ == name:
                return self.delete_model(obj)

    @action("fetch_search_doc")
    def fetch(self, doc_type, id, index=None, **kwargs):
        index = self.get_index(doc_type, index)
        return self.es.get(index=index, doc_type=doc_type, id=id, **kwargs)

    @action(as_="search_results")
    def search(self, doc_type, index=None, paginate=False, page=None, obj_loader=None, **kwargs):
        index = self.get_index(doc_type, index)
        per_page = 10 # pyelasticsearch's default
        if not kwargs:
            kwargs["q"] = request.args.get("q")
        if paginate:
            if not page:
                page = int(request.args.get("page", 1))
            per_page = self.options["pagination_per_page"] if isinstance(paginate, bool) else paginate
            kwargs["from_"] = (page - 1) * per_page
            kwargs["size"] = per_page
        current_app.logger.debug("Performing search %s in %s/%s" % (kwargs, index, doc_type))
        try:
            res = self.es.search(index=index, **kwargs)
        except Exception as e:
            current_app.logger.error(e)
            res = None
        return SearchResults(res, kwargs.get("q"), per_page, page, obj_loader)

    @action(as_="search_results", default_option="model")
    def search_model(self, model, **kwargs):
        if isinstance(model, str):
            model = current_app.features.models[model]
        def obj_loader(hit):
            if self.options["use_redis_partial_models"]:
                return current_app.features.redis.get_partial_model_from_cache(model, hit['_id'])
            return current_app.features.models.query(model).get(hit["_id"])
        return self.search(model.__name__.lower(), _source=False, obj_loader=obj_loader, **kwargs)

    @action(as_="suggestions")
    def autocomplete(self, doc_type, field, text, index=None):
        index = self.get_index(doc_type, index)
        field = "suggest_%s" % prop
        body = {"autocomplete", {"text": text, "completion": {"field": field}}}
        try:
            res = self.es.suggest(index=index, body=body)
        except Exception as e:
            current_app.logger.error(e)
            return []
        if "autocomplete" not in res:
            current_app.logger.error(res)
            return []
        suggestions = []
        for option in res["autocomplete"][0]["options"]:
            suggestions.append((option["text"], option["payload"]["id"]))
        return suggestions

    def autocomplete_endpoint(self, doc_type=None, field=None, text=None):
        doc_type = doc_type or request.args["doc_type"]
        field = field or request.args["field"]
        text = text or request.args["text"]
        return Response(json.dumps(self.autocomplete(doc_type, field, text)), mimetype="application/json")


class SearchResults(object):
    def __init__(self, results, q=None, per_page=10, page=1, obj_loader=None):
        self.results = results
        self.q = q
        self.total = results["hits"]["total"] if results else 0
        self.per_page = per_page
        self.nb_pages = int(math.ceil(float(self.total) / float(per_page)))
        self.page = page
        self.hits = results["hits"]["hits"] if results else []
        self.obj_loader = obj_loader

    def __iter__(self):
        for hit in self.hits:
            if self.obj_loader:
                obj = self.obj_loader(hit)
                if obj:
                    yield obj
            else:
                yield AttrDict(hit)

    def for_json(self):
        return list(self)

    @property
    def prev_page(self):
        return self.page - 1 if self.page > 1 else None

    @property
    def next_page(self):
        return self.page + 1 if self.page < self.nb_pages else None

    # code from Flask-Sqlalchemy
    # https://github.com/mitsuhiko/flask-sqlalchemy/
    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.nb_pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.nb_pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

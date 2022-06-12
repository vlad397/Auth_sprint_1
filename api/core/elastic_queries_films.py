def get_filter_genre_query(filter_genre):
    return {
        "query": {
            "bool": {
                "filter": [
                    {
                        "nested": {
                            "path": "genres",
                            "query": [
                                {"match": {"genres.uuid": filter_genre}}
                            ],
                        }
                    }
                ]
            }
        }
    }


def get_query_for_match_all():
    return {"query": {"match_all": {}}}


def get_search_film_query(search_text):
    return {
        "query": {
            "multi_match": {
                "query": search_text,
                "fields": ["title", "description"]
            }
        }
    }

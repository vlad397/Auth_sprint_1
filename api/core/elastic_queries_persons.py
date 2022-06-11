def get_persons_movies_query(person_ids: list):
    return {
        "query": {
           "bool": {
              "should": [
                   {
                       "nested": {
                         "path": "actors",
                         "query": {
                             "terms": {
                                 "actors.uuid": person_ids
                             }
                         }
                       }
                   },
                   {
                       "nested": {
                         "path": "directors",
                         "query": {
                             "terms": {
                                 "directors.uuid": person_ids
                             }
                         }
                       }
                   },
                   {
                      "nested": {
                          "path": "writers",
                          "query": {
                              "terms": {
                                  "writers.uuid": person_ids
                              }
                          }
                      }
                   }
              ]
           }
        }
    }


def get_persons_search_query(search_text):
    return {
        "query": {
            "match": {
                "full_name": {
                    "query": search_text
                }
            }
        }
    }

(require processor.utils.macro)
(require hy.contrib.anaphoric)

(import urllib)

(import [processor.storage [get-storage]])
(import [processor.utils [merge-dicts]])
(import [itertools [takewhile]])
(import [twiggy_goodies.threading [log]])


(defn rate-limited [data]
  "Checks if response from twitter contains error because rate limit was exceed."
  (ap-if (.get data "errors")
         (when (= (get (get it 0) "code")
                  88)
           (log.warning "Rate limited")
           True)
         False))


(defn search [query &optional consumer_key consumer_secret access_token access_secret]
  (import-or-error [requests_oauthlib [OAuth1Session]]
                   "Please, install 'requests-oauthlib' to use 'twitter.search' source.")
  
  (defn add-source-and-type [tweet]
    (merge-dicts tweet {"source" "twitter.search"
                        "type" "twitter.tweet"}))
  
  (with-log-name-and-fields "twitter-search" {"query" query}
    (setv [get-value set-value] (get-storage "twitter-search"))
    (setv seen-id-key (.join ":" [query "seen-id"]))
    (setv seen-id (get-value seen-id-key 0))
    
    (setv url (+ "https://api.twitter.com/1.1/search/tweets.json?"
                 (urllib.parse.urlencode {"q" query})))
    (setv twitter (apply OAuth1Session []
                          {"client_key" consumer_key
                           "client_secret" consumer_secret
                           "resource_owner_key" access_token
                           "resource_owner_secret" access_secret}))
    (log.info "Searching in twitter")
    (setv response (twitter.get url))
    (setv data (response.json))

    
    (unless (rate-limited data)
      (setv metadata (get data "search_metadata"))
      (setv max-id (get metadata "max_id"))
      (setv statuses (get data "statuses"))
      (setv new-statuses (genexpr (add-source-and-type item)
                                  [item statuses]
                                  (> (get item "id")
                                     seen-id)))
      (set-value seen-id-key max-id)
      
      (yield-from new-statuses))))


(defn followers [&optional consumer_key consumer_secret access_token access_secret]
  (import-or-error [requests_oauthlib [OAuth1Session]]
                   "Please, install 'requests-oauthlib' to use 'twitter.followers' source.")

  (defn add-source-and-type [tweet]
    (merge-dicts tweet {"source" "twitter.followers"
                        "type" "twitter.user"}))

  (with-log-name "twitter-followers"
    (setv [get-value set-value] (get-storage "twitter-followers"))
    (setv seen-key "seen")
    (setv seen (set (get-value seen-key (set))))
    
    (setv url "https://api.twitter.com/1.1/followers/list.json?count=200")
    (setv twitter (apply OAuth1Session []
                          {"client_key" consumer_key
                           "client_secret" consumer_secret
                           "resource_owner_key" access_token
                           "resource_owner_secret" access_secret}))
    (log.info "Fetching followers from twitter")

    (defn fetch-data [cursor]
      (setv page-url (+ url (if cursor
                              (+ "&cursor=" (str cursor))
                              "")))
      (print "Fetching:" page-url)
      (setv response (twitter.get page-url))
      (setv data (response.json))
      (unless (rate-limited data)
        (setv users (get data "users"))
        (when users
          (yield-from users)
          (setv next-cursor (get data "next_cursor"))
          (print "next-cursor:" next-cursor)
          (if next-cursor
              (yield-from (fetch-data next-cursor))))))


    (setv new-followers (takewhile (fn [user] (not (in (get user "id")
                                                       seen)))
                                   (fetch-data 0)))
    (setv new-followers-ids (list-comp (get item "id")
                                       [item new-followers]))

    (.update seen new-followers-ids)
    (set-value seen-key (list seen))
    
    (yield-from (map add-source-and-type
                     new-followers))))

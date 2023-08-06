(require processor.utils.macro)

(import codecs)
(import [hashlib [md5]])
(import [processor.storage [get-storage]])

;; Uses http://lkiesow.github.io/python-feedgen/

(defn create-feed [data &optional
                   [title "Rss Feed"]
                   [description "Without description"]
                   [link "no link"]]
  (import-or-error [feedgen.feed [FeedGenerator]]
                   "Please, install 'feedgen' library to use 'rss' output.")

  (setv feed (FeedGenerator))
  (.title feed title)
  (.link feed {"rel" "alternate"
               "href" link})
  (.description feed description)
  
  (for [item data]
    (setv feed-item (.add_entry feed))
    (setv item-title (get item "title"))
    (setv item-id (or (.get item "id")
                      (.hexdigest (md5 (.encode item-title "utf-8")))))
    (setv item-body (.get item "body"))
    
    (.id feed-item item-id)
    (.title feed-item item-title)
    (if item-body
      (.description feed-item item-body)))
  
  (apply .rss_str [feed] {"pretty" True}))


(defn rss [filename &optional [limit 10]]
  "Accepts dicts with fields
   - title
   - body
  "
  (setv [get-value set-value] (get-storage "rss-target"))
  
  (defn rss-updater [obj]
    (setv data (get-value filename []))
    
    (.append data obj)
    (setv data (slice data (- limit)))
    
    (set-value filename data)
    
    (with [[f (codecs.open filename "w" "utf-8")]]
          (.write f (create-feed data)))))

(setv _handles {})

(defn web-hook [handle]
  (setv values [])
  (assoc _handles handle (fn [item] (.append values item)))
  
  (defn get-webhook-values []
    (setv result (.copy values))
    (.clear values)
    result)
  )

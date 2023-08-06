(import [collections.abc [Iterable]])


(defn extract_messages [sources]
    """Returns messages, taking
    them one by one from each source.

    If source returns None, then it
    should be skipped.
    """
    (setv sources (list (map iter sources)))
    (setv idx 0)

    (while sources
      (setv source (get sources idx))
      
      (try
       (setv value (next source))
       
       (catch [e StopIteration]
         (del (get sources idx)))
       
       (else
        (lisp-if value
                 (yield value))
        (setv idx (+ idx 1))))

      (if (>= idx (len sources))
        (setv idx 0))))


(defn run-action [actions msg]
  (if-not (isinstance actions Iterable)
    (setv actions [actions]))
  
  (for [action actions]
    (setv msg (action msg))
    (if-not msg
            (break)))
  msg)


(defn make-generator [func]
  "Makes generator from a function,
calling it until it return None and yielding returned values"
  (setv value (func))
  (while (not (is_none value))
    (yield value)
    (setv value (func))))


(defn run_pipeline [sources rules]
  (setv sources (list-comp
                 (if (callable s)
                   (make-generator s)
                   s)
                 [s sources]))
  (for [msg (extract_messages sources)]
    (for [(, trigger action) rules]
      (if (trigger msg)
        (run-action action msg)))))

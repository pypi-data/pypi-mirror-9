;; Additional flow macros

(defmacro/g! guard [&rest args]
  (setv g!cond (car args))
  (setv g!body (car (cdr args)))
  (setv g!rest (cdr (cdr args)))
  (if g!rest
  `(if ~g!cond
       ~g!body
       (guard ~@g!rest))
  `(if ~g!cond
       ~g!body)))

(defmacro/g! switch [variable &rest args]
  (setv g!comp (car args))
  (setv g!body (car (cdr args)))
  (setv g!rest (cdr (cdr args)))
  (setv g!cond `(~(car g!comp) ~variable ~@(cdr g!comp)))
  (if g!rest
      (if (cdr g!rest)
        `(if ~g!cond ~g!body (switch ~variable ~@g!rest))
        `(if  ~g!cond ~g!body ~@g!rest))
      `(if  ~g!cond ~g!body)))
  

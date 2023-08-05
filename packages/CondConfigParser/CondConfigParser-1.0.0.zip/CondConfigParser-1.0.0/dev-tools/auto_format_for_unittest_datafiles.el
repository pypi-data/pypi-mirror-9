(defun flo-custom-replace-1-internal (start-marker end-marker)
  (save-excursion
    (goto-char start-marker)
    (query-replace-regexp
     "\\(condconfigparser\\.parser\\.\\)\\([a-zA-Z_0-9]+\\)\\(Node(\\)"
     "p.\\2\\3\n"
     nil start-marker end-marker)

    (goto-char start-marker)
    (query-replace "condconfigparser.lexer." "l." nil start-marker end-marker)

    (goto-char start-marker)
    (query-replace-regexp
     "\\(p\\.\\(BoolLiteral\\|StringLiteral\\|Variable\\)Node(\\)[ \n]*" "\\1"
     nil start-marker end-marker)

    (goto-char start-marker)
    (query-replace "), p." "),\np." nil start-marker end-marker)

    (goto-char start-marker)
    (query-replace "], [p." "],\n[p." nil start-marker end-marker)

    (goto-char start-marker)
    (insert "refTree = \\\n")
    (indent-region start-marker end-marker)))

(defun flo-custom-replace-1 (start end)
  (interactive "r")
  (let ((start-marker (make-marker))
        (end-marker (make-marker)))
    (unwind-protect
        (progn
          (set-marker start-marker start)
          (set-marker end-marker end)
          (python-mode)
          (flo-custom-replace-1-internal start-marker end-marker))
      (dolist (marker (list start-marker end-marker))
        (unless (null marker)
          (set-marker marker nil))))))

(global-set-key (kbd "<s-pause>") 'flo-custom-replace-1)

# loan_application_classifier

Document name + OCR text → classified type (paystub / W2 / bank-stmt / tax
return / ID …) + extracted fields + completeness flag.

```bash
uv run python recipes/loan_application_classifier/recipe.py \
  --document-name "borrower_paystub_march.pdf" --text "$(cat ocr.txt)"
```

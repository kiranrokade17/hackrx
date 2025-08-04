# 🚨 JSON DECODE ERROR - INSTANT FIX

## ERROR: "Extra data" at position 47
This means there's invalid JSON syntax around character 47 in your request body.

## ✅ COPY THIS EXACT JSON (NO MODIFICATIONS):

### Single Question Test:
```json
{
    "documents": "D:/document/resume kiran.pdf",
    "questions": [
        "What skills does Kiran Rokade have?"
    ]
}
```

### Multi-Question Test:
```json
{
    "documents": "D:/document/resume kiran.pdf",
    "questions": [
        "What skills does Kiran Rokade have?",
        "What is Kiran's educational background?",
        "What work experience does Kiran have?",
        "What is Kiran's current job role?"
    ]
}
```

## 🔧 POSTMAN STEPS:
1. **Clear Body**: Delete everything in Body tab
2. **Select**: Body → raw → JSON (not Text!)
3. **Copy-Paste**: Use exact JSON above
4. **Headers**: 
   - Content-Type: application/json
   - Authorization: Bearer api_key_1
5. **Send**: Should work immediately

## ❌ COMMON MISTAKES CAUSING THIS ERROR:
- Extra comma after last question: `"question"?,`
- Missing quotes: `documents:` instead of `"documents":`
- Wrong brackets: `}` instead of `]`
- Hidden characters from copy-paste
- Selecting "Text" instead of "JSON" in dropdown

## 💡 VALIDATION TIP:
Paste your JSON into https://jsonlint.com/ to check for syntax errors before using in Postman.

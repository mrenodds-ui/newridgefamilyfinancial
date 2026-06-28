# NewRidgeFinancial 2.0

Standalone mission-control program for New Ridge Family Financial.

The legacy program in `_legacy/` is for reference only and is not used here.

## Run

Double-click `StartNewRidgeFinancial2.bat` (repo root), or run
`scripts\start_nr2_1966.ps1`.

**URL:** http://127.0.0.1:1966/

## Files

```
NewRidgeFinancial2/
  site/
    index.html        sidebar + page viewer
    styles.css        mission-control shell styling
    app.js            switches between the 9 program pages
    pages/            the 9 mission-control page images
  serve.py            static file server on port 1966
```

## Stop

`StopNewRidgeFinancial2.bat`

# Database for SRF cavities
This project wants to be a database of the test results of SRF cavities

> [!WARNING]
>
> The project is in an early phase... Much could be wrong and much will change

The main idea is the following:
1. Use a combination of `python` + `SQLite` to collect the data
2. Use a `python` based UI to query, browse and visualize the data

As of right now the data can be inserted in few different ways

The endgoal is an _automatic_ collection of all the info inside the `data` folder

## Use
If data.db is missing or outdated run `python collect_database.py`

To open the browsing UI run `streamlit run app.py`

> [!IMPORTANT]
>
> This second command will depend on the UI design
>
> Currently `sltreamlit` is being used but this might change

## Requirements
In addition to a working `python` installation (`sqlite3` should be in `python3`), you will need 
```
pip install pandas matplotlib streamlit
``` 
As Mentioned, `sltreamlit` might be later dropped in favour of another UI

## Structure
The aim is to structure the project as follows (please ignore the temporary test files) 

```
📁 SRF_database
├── 📄 README.md
├── 🐍 collect_database.py
├── 🐍 app.py
├── 📁 data
│ ├── 📁 cavity1
│ │ ├── 📄 metadata.json
│ │ ├── 📄 cavity1_data.txt
│ │ ├── 🖼️ plot1.png
│ │ ...
│ │ └── 🖼️ plotn.png
│ ├── 📁 cavity2
│ ...
```

The final structure of the `data.txt` is still under discussion

The structure of the `metadata.json` will probably resemble something like this

```
{
  "experiment_name": "FG004_throughTc",
  "lab_name": "Lab A",
  "description": "Lore lipsium (data + plot)",
  "date": "2025-04-01",
  "article_url": "https://arxiv.org/abs/2401.12342"
}
```

What information will be stored in the metadata is under discussion


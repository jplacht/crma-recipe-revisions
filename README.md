# Salesforce CRM Analytics Recipe Field Comparator 

This repository contains a small Python script that works with Salesforce CRM Analytics `.wdpr` files located in the recipes directory. Upon each run, the script creates a revision and compares the fields in the given recipe folder. It outputs the current list of all used fields in any recipe as well as a comparison of objects that have fields removed or added.

## Features

- CLI usage allowed
- Creates revisions of recipe files.
- Compares fields between different revisions.
- Outputs current list of all used fields.
- Highlights objects with fields removed or added.

## Installation

1. Install Python (developed with Python 3.10)
2. Install Python dependencies with your manager or `pip` by using `pip install -r requirements.txt`
3. Run the script with `python main.py` to see its options

## CLI

The scripts CLI allows the following commands to easily be executed:

1. `python main.py init` - initializes the specified recipe and/or revision folder if not already present
2. `python main.py run` - creates a new revision
3. `python main.py show` - shows a list of available revisions
3. `python main.py show [REVISION ID] [true/false]` shows a specific revision either with used SFDC objects or only showing changes compared to previous version

Use `python main.py --help` for a list of available options.

## .env

The recipe field comparator is by default creating / looking for the `/revisions` and `/recipes` folders to work with. You can overwrite this by creating your own .env file and specifying other folders on your machine. An example can be found in `.env-example`.

## Example Revision

```shell
> python main.py show

Revisions:
[1] 	 2024-04-04T11:45:34.759927 	 4a62b60c-30ba-4145-bae5-1d9a652a0246 	 <- 7d365e83-745d-47d0-962c-1d7c4ce89173
[2] 	 2024-04-04T11:46:34.784859 	 af128890-28e5-4fff-9700-baca04d901db 	 <- 4a62b60c-30ba-4145-bae5-1d9a652a0246
[3] 	 2024-03-27T12:02:36.895133 	 7d365e83-745d-47d0-962c-1d7c4ce89173

```

## Example JSON

```json
{
	"revision": "05e3767d-eb55-4375-8913-1734382c9d59",
	"previous": "02a03999-9461-42ec-ad78-b520ab0ca3b0",
	"created": "2024-03-27T11:57:40.996602",
	"comparison": [
		{
			"name": "CustomObject_Test__c",
			"additions": ["LastModifiedDate"],
			"removals": ["CreatedDate"]
		}
	],
	"current_fields": {
		"CustomObject_Test__c": [
            "Id", 
            "LastModifiedDate"
        ]
	}
}
```

# License

MIT

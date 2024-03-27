# Salesforce CRM Analytics Recipe Field Comparator 

This repository contains a small Python script that works with Salesforce CRM Analytics `.wdpr` files located in the `/recipes` directory. Upon each run of `python runner.py`, the script creates a revision and compares the fields in the given recipe folder. It outputs the current list of all used fields in any recipe as well as a comparison of objects that have fields removed or added.

## Features

- Creates revisions of recipe files.
- Compares fields between different revisions.
- Outputs current list of all used fields.
- Highlights objects with fields removed or added.

## Example Output

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
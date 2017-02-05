# runningahead_analytics
Code to retrieve analytics

## Installation & Use Notes
* Install fresh environment and activate it
* Install all program packages with: pip install -r requirements.txt
* Run python main.py
* Repeat previous command each time you want to check and add new records

##Notes:
Create new "settings" directory in program root folder.
Add into settings directory following files:
* access_tokens.json
* Analytics Code-d9b5f2ff02e5.json

###access_tokens.json template:
{
  "some_runningahead_account1": "xxxxyyyyzzzz",
  "some_runningahead_account2": "zzzzyyyyxxxx"
}

###Analytics Code-d9b5f2ff02e5.json
Obtained from google drive api
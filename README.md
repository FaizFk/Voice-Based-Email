# Voice Based Email

This is a email system that might help visually impaired people to let them manage their gmail.
Right now, this allows you to Get Latest Emails, Compose an Email, Search the Emails.

## Installation

#### 1. Install required packages

```bash
  pip install -r requirements.txt
```

<i> Note: While running the script if it asks for any other modules, just install them too </i>

#### 2. Get credentials.json file

   There is a credentials.json file in the folder, but right now most of it's field are empty. Get the credentials.json file from Google Gmail API. Follow these <a     href="https://developers.google.com/gmail/api/quickstart/python">steps</a> and replace the credentials.json file.

#### 3. Run the script

```bash
  python VEC.py
```
<i> When you run the script first time, you will be asked to login using consent screen, this will create a token file in folder </i>

## Some Tips

1. When saying email I found it better to say it letter by letter, then the script will handle all the spacing
2. I have created MAPPINGS dictionary that maps the special characters. To say any special character just add the word "character" after that while saying it.
   For Example to say "." just say "dot character".

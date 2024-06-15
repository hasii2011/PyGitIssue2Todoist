
```bash
pip install buildlackey
```

You must first create the OS X app by running the `package` python script

```bash
packageme
```

Then follow the instructions at the [Py2App Code Signing Repository](https://github.com/hasii2011/py2appsigner)



Something like this:

```bash
 
 py2appSign -p 3.11 -d PyGitIssue2Todoist -a PyGitIssue2Todoist  zipsign
 py2appSign -p 3.11 -d PyGitIssue2Todoist -a PyGitIssue2Todoist  appsign
 appNotarize -d PyGitIssue2Todoist -a PyGitIssue2Todoist --verbose
 appStaple -d PyGitIssue2Todoist -a PyGitIssue2Todoist --verbose
 appVerify -d PyGitIssue2Todoist -a PyGitIssue2Todoist --verbose
```

If you get any errors do:

```bash
notaryTool information -i <submission ID	# from the appNotarize step
```


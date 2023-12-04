# Overview

Action to create a badge for a github reusable workflow. When using reusable workflows github does not create a workflow badge. This action will create a badge for the workflow and commit the badge to git for reference in README.md.

The service [badgen.net](https://badgen.net) is used to render the badge.


## Example Usage

Given a workflow (workflow.yml) that executes on push events

```yaml
# workflow.yml

name: Test workflow badge action

on:
  push:
    branches:
    - '*'
    - '!badges'
  workflow_dispatch:
        
jobs:

  test:
    name: test workflow badge
    uses: ./.github/workflows/echo.yml

```

and a reusable workflow (echo.yml)

```yaml
# echo.yml
name: test echo

on:
  workflow_call:
  
jobs:
  echo:
    name: test echo
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Echo command
      id: echo
      shell: bash
      run: echo "Hello World"

    # Create badge for the preceding step
    - name: create badge
      uses: srfoster65/workflow_badge_action@main
      with:
        label: ${{ github.job}}
        status: ${{ steps.echo.outcome }}

```

To apply to your workflow:

in the main workflow, ensure the workflow does not run when commiting changes to the badges branch

```yaml
on:
  push:
    branches:
    - '*'
    - '!badges'

```

Then in the reusable workflow , call workflow_badge_action using the name of the job as the label and the outcome of the actual test case ("echo" in the example below) as the status.

```yaml
    - name: create badge
      uses: srfoster65/workflow_badge_action@main
      with:
        label: ${{ github.job}}
        status: ${{ steps.echo.outcome }}
```

## Input Options

### Label

Required parameter.  
The text applied to the left hand side of the badge, and is also used to name the badge.

### Status

Required parameter.  
If status is a known output from a workflow outcome, the text and colour of the badge will be set as follows.

| Status   | Badge Status | Colour |
| -------- | ------------ | ------ |
| success  | Passing      | green  |
| failure  | Failing      | red    |
|cancelled | Cancelled    | grey   |
| skipped  | Skipped      | grey   |

Any other value will be displayed without modification

### Colour

Colour can be a hex value or named colour. If a value is supplied it will override default behaviour.  
Default behaviour is to use a colour mapping if status is matches a known value, else default to blue.

See [here](https://badgen.net/help#options) for named colours supported.

### Icon

Icon can be a named icon. If a value is supplied it will override default behaviour.  
If no icon is specified, a github icon will be applied to the badge. If no icon is required then icon should be specifed with no value when calling the action.

See [here](https://badgen.net/help#options) for named icons supported.

### Badges Branch

Badges_branch can be speciifed to allow committing badges to a named branch.  
If no value is supplied, the branch "badges" is used.

### Label Colour

Label_colour can be a hex or named colour. If a value is supplied it will override default behaviour.  
If no value is supplied, label colour grey is used.

## Outputs

The generated badge is committed to badges_branch (Default: badges)

It is saved to: ./[working_branch]/[label].svg

where:

- working_branch: The current git branch
- label: The left hand text of the badge

The badge can be referenced using the following URL:

https://raw.githubusercontent.com/[github account]/[github project]/badges/[*branch*]/[*label*].svg

e.g.  
Use the following markdown in README.md to render a badge named test, on main.

```text
![svg badge](https://raw.githubusercontent.com/srfoster65/workflow_badge_action/badges/main/test.svg)
```

![svg badge](https://raw.githubusercontent.com/srfoster65/workflow_badge_action/badges/main/test.svg)

This action uses [badge-action](https://github.com/marketplace/actions/badge-action) to generate the svg image.

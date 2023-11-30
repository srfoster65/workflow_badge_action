# Overview

Create an svg badge and commit the image to git. A separate branch (badges) is used for the commit to avoid poluting the development branch.

The badge is saved to: ./[working_branch]/[label].svg

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

The colors you can use with query param: ?color=[colorname]

blue cyan green yellow orange red pink purple grey black

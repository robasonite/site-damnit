---
title: YAML lists
date: 2020-08-19 01:01:01
custom-list:
  - apples
  - bananas
  - oranges
---

This is a demo page to test (and hopefully show off!) the ability to add custom YAML to your front matter.

<br/>

**Raw HTML**

<ul>
{{#custom-list}}
  <li>{{name}}</li>
{{/custom-list}}
</ul>
<br/>

**Markdown**

{{#custom-list}}
* {{name}}
{{/custom-list}}

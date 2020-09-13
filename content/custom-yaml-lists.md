---
title: Custom YAML lists
date: 2020-08-19 01:01:01
custom-list:
  - apples
  - bananas
  - oranges
---

This is a demo page to test (and hopefully show off!) the ability to add custom YAML to your front matter.

## Raw HTML

<ul>
{{#custom-list}}
  <li>{{name}}</li>
{{/custom-list}}
</ul>

## Markdown

{{#custom-list}}
* {{name}}
{{/custom-list}}

---
layout: default
title: "Founder Engineering Field Notes"
permalink: /
---

# Founder Engineering Field Notes

Practical engineering lessons based on verified software work: real failure signatures, actual root causes, minimal validated corrections, and the controls that should have caught the problem earlier.

{% if site.data.articles.size > 0 %}
## Published field notes

{% for article in site.data.articles %}
### [{{ article.title }}]({{ article.url | relative_url }})

{{ article.summary }}

_Verified against current public documentation: {{ article.verified_on }}_
{% endfor %}
{% else %}
No articles have been editorially approved for publication yet.
{% endif %}

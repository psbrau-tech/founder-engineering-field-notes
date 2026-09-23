---
layout: default
title: "Categories"
permalink: /categories/
---

# Categories

Browse published field notes by engineering track.

## Cloud & Delivery

{% assign found = false %}
{% for article in site.data.articles %}
{% if article.categories contains "cloud-delivery" %}
{% assign found = true %}
- [{{ article.title }}]({{ article.url | relative_url }}) — {{ article.summary }}
{% endif %}
{% endfor %}
{% unless found %}_No published field notes yet._{% endunless %}

## Stateful Product Engineering

{% assign found = false %}
{% for article in site.data.articles %}
{% if article.categories contains "stateful-product-engineering" %}
{% assign found = true %}
- [{{ article.title }}]({{ article.url | relative_url }}) — {{ article.summary }}
{% endif %}
{% endfor %}
{% unless found %}_No published field notes yet._{% endunless %}

## AI Product Operations

{% assign found = false %}
{% for article in site.data.articles %}
{% if article.categories contains "ai-product-operations" %}
{% assign found = true %}
- [{{ article.title }}]({{ article.url | relative_url }}) — {{ article.summary }}
{% endif %}
{% endfor %}
{% unless found %}_No published field notes yet._{% endunless %}

## Founder Engineering Discipline

{% assign found = false %}
{% for article in site.data.articles %}
{% if article.categories contains "founder-engineering" %}
{% assign found = true %}
- [{{ article.title }}]({{ article.url | relative_url }}) — {{ article.summary }}
{% endif %}
{% endfor %}
{% unless found %}_No published field notes yet._{% endunless %}

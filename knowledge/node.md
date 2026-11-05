---
id: root
kind: ka:Root
title: Knowledge architecture
status: proposed
origin: template
pointers:
  - kind: ka:TextPointer
    target: digital-product-development
    trigger: You plan, design, or build a digital product.
  - kind: ka:PathPointer
    target: governance
    trigger: You change a node file.
    paths:
      - knowledge/**
      - skills/**
      - governance/**
---

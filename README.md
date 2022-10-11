<p align="center">
    <img src="https://raw.githubusercontent.com/NannyML/nannyml/main/media/thumbnail-4.png">
</p>
<p align="center">
    <a href="https://pypi.org/project/nannyml/">
        <img src="https://img.shields.io/pypi/v/nannyml.svg" />
    </a>
    <a href="https://anaconda.org/conda-forge/nannyml">
        <img src="https://anaconda.org/conda-forge/nannyml/badges/version.svg" />
    </a>
    <a href="https://pypi.org/project/nannyml/">
        <img src="https://img.shields.io/pypi/pyversions/nannyml.svg" />
    </a>
    <a href="https://github.com/nannyml/nannyml/actions/workflows/dev.yml">
        <img src="https://github.com/NannyML/nannyml/actions/workflows/dev.yml/badge.svg" />
    </a>
    <a href='https://nannyml.readthedocs.io/en/main/?badge=main'>
        <img src='https://readthedocs.org/projects/nannyml/badge/?version=main' alt='Documentation Status' />
    </a>
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/nannyml?color=green" />
    <br />
    <br />
    <a href="https://www.producthunt.com/posts/nannyml?utm_source=badge-top-post-badge&utm_medium=badge&utm_souce=badge-nannyml" target="_blank">
        <img src="https://api.producthunt.com/widgets/embed-image/v1/top-post-badge.svg?post_id=346412&theme=light&period=daily" alt="NannyML - OSS&#0032;Python&#0032;library&#0032;for&#0032;detecting&#0032;silent&#0032;ML&#0032;model&#0032;failure | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" />
    </a>

</p>

<p align="center">
    <strong>
        <a href="https://nannyml.com/">Website</a>
        •
        <a href="https://nannyml.readthedocs.io/en/stable/">Docs</a>
        •
        <a href="https://join.slack.com/t/nannymlbeta/shared_invite/zt-16fvpeddz-HAvTsjNEyC9CE6JXbiM7BQ">Community Slack</a>
    </strong>
</p>

# NannyML examples

This repository contains some ready-to-run examples, showcasing some ways to run NannyML and integrate 
with third-party tools. Each example can be run by itself. 

## Integration examples

### Drift and performance dashboards in Grafana

These examples process all model inputs/outputs using the containerized NannyML CLI. 
The results are stored in a relational database. We read the data from the metrics database and 
visualize them in two Grafana dashboards.

We have examples for the following problem types:

- [Binary classification](regression)
- [Multiclass classification](multiclass_classification)
- [Regression](regression)

### Incremental drift and performance dashboards in Grafana

These incremental examples are a slight variation of the previous ones. They will not process all the data at once, 
but will simulate running NannyML in a scheduled way. 

We have examples for the following problem types:

- [Regression](regression_incremental)
.DEFAULT_GOAL := help

.PHONY: build dev idea ideas new draft-from-idea process publish add-image clean deploy \
	test check format lint install help

build: ## build the static site
	blog build


dev: ## start development server with live reload
	blog dev


# args: title
idea: ## capture a new idea in the inbox
	blog idea "$(TITLE)"


ideas: ## list captured ideas
	blog ideas


# args: title
new: ## create a new draft article
	blog new "$(TITLE)"


# args: idea-name
draft-from-idea: ## start a draft from an idea note
	blog draft-from-idea $(IDEA_NAME)


# args: filename
process: ## resolve AI instruction placeholders in a draft
	blog process $(FILENAME)


# args: filename
publish: ## publish a draft article
	blog publish $(FILENAME)


# args: post-name image-name source
add-image: ## add an image to a draft post
	blog add-image "$(POST_NAME)" "$(IMAGE_NAME)" "$(SOURCE)"


clean: ## clean generated files
	blog clean


deploy: ## deploy to Netlify
	blog deploy


test: ## run unit tests and check internal links
	blog test


check: ## build and test before deployment
	blog check


format: ## format code using ruff
	blog format


lint: ## lint code using ruff
	blog lint


install: ## install dependencies
	uv pip install -e .


help: ## show available tasks
	@awk 'BEGIN {FS = ": ## "} /^[a-zA-Z0-9_.-]+: ## / {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: test

test:
	nosetests

clean:
	find . -name "*.pyc" | xargs rm -f
	find . -name "*~" | xargs rm -f
	rm -rf .coverage *,cover build dist *egg-info


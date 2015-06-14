
generate:
	python generate.py

upload:
	cd site; rsync -avz --delete . df:/var/web/groups/lec2/soma --exclude=.*

update:
	git pull
	generate
	upload    

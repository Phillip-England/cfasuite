# vars
TAILWIND_INPUT = ./static/css/input.css
TAILWIND_OUTPUT = ./static/css/output.css

# running "make" will run this command
all: build

# The build target runs the TailwindCSS command
tw:
	tailwindcss -i $(TAILWIND_INPUT) -o $(TAILWIND_OUTPUT) --watch

# kills all activity on port 8080
kill:
	sudo lsof -t -i:8080 | xargs kill -9

run:
	air

install:
	flint spark; mv out ..; cd ..; mv out www.philthy.blog; cd www.philthy.blog; rm -r index.html; rm -r post; rm -r posts.html; rm -r screenplay.html; rm -r favicon.ico; rm -r static; cd out; mv * ..; cd ..; rm -r out;
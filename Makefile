.PHONY: build

build:
	mkdir -p ./build
	blender --command extension build \
		--source-dir ./io_scene_kotor \
		--output-dir ./build

clean:
	rm -f build/*

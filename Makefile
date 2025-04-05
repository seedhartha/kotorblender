.PHONY: build test

build:
	mkdir -p ./build
	blender --command extension build \
		--source-dir ./io_scene_kotor \
		--output-dir ./build

test:
	blender --background --python ./test/test_models.py

clean:
	rm -rf build/*
	rm -rf test/out/*

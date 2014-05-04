override DEBUG = false

.PHONY: all js jade

JS_DIR = js
JS_TARGET = $(JS_DIR)/rapidfire.js
JS_DEPS = $(filter-out $(JS_TARGET), $(wildcard $(JS_DIR)/*.js))

all: js
js: $(JS_TARGET)


$(JS_TARGET): $(JS_DEPS)
	cat $^ > $@

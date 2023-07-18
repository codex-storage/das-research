.PHONY: test clean

CC := g++
FLAGS := -Wall -std=c++11 -shared -fPIC
FLAGS += -undefined dynamic_lookup
INC := $(shell python3 -m pybind11 --include)
SUFFIX := $(shell python3-config --extension-suffix)

CC_FILE := DAS/deque.cc
OBJ := DAS/deque$(SUFFIX)

$(OBJ): $(CC_FILE)
	$(CC) $(FLAGS) $(INC) $< -o $(OBJ)
clean:
	rm *.so
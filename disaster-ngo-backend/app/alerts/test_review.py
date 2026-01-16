from review import human_review_required

if __name__ == "__main__":
    print(human_review_required(0.9, 0.9, 0.8))  # False
    print(human_review_required(0.9, 0.3, 0.8))  # True
    print(human_review_required(0.5, 0.9, 0.9))  # True

from discogs_collection import DiscogsCollection


def main():
    print("Ran Main Randomboye")
    my_collection = DiscogsCollection("CWhLmAdMsIhLXCeIfCXDZszstBbeWxbsTlmvntFf")
    my_collection.get_random_record()


if __name__ == '__main__':
    main()

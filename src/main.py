from src.utils import search_book, check_availability

# Dictionary to store previously searched books
previous_searches = {}


# Main interaction loop
def main():
    while True:
        title = input("Enter the book title to search (or 'exit' to quit): ")
        if title.lower() == "exit":
            break

        library = input("Enter the library branch you're interested in: ")

        # Check if the book has been searched before
        if title in previous_searches:
            check_availability(previous_searches[title], library)
        else:
            search_book(title, library)


# Run the main function
main()

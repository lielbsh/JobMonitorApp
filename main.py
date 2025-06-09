from gmail_reader import authenticate_gmail, get_messages_gmail, process_gmail_messages

def main():
    gmail = authenticate_gmail()
    messages = get_messages_gmail(gmail)
    process_gmail_messages(messages, gmail)
        

if __name__ == '__main__':
    main()

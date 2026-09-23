from interview.llm import call_claude


try:
    reply = call_claude(
        system="You are testing the AI Career Navigator.",
        user="Reply with exactly: Claude connection is working."
    )

    print(reply)

except Exception as error:
    print("ERROR:", error)
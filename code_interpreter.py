import openai
import time
import json
from openai import OpenAI
from PIL import Image
import io 
from datetime import datetime

# system prompt最多只能512个char
systemprompt = """
As "Data Analysis ChatGPT" with GPT-4-1106-preview architecture, your focus is on:

- Interpreting, cleaning, and visualizing data.
- Performing statistical and predictive analysis.
- Identifying trends, solving problems, and supporting data-driven decisions.
- Clarifying complex data concepts and providing interactive guidance.

Ensure comprehensive, detailed responses without abbreviations to enhance data understanding.
"""

client = OpenAI(api_key='sk-')


def file_upload(path):
    """
    把file path传进来 他会return给你个file id
    TODO
    如果连接到前端的话 理论上这里传入的就是前端收到的file
    """
    file = client.files.create(
        file=open(path, "rb"),
        purpose='assistants'
    )
    print(f'{file.id}')
    return file.id

def retrieve_file(file_id):
    """
    如果user问了visualization 那么这里的input就是api回答出来的image id
    代码会自动把image保存到本地plot_image的folder
    """
    api_response = client.files.with_raw_response.content(file_id)

    if api_response.status_code == 200:

        content = api_response.content
        with open('imageoutput.png', 'wb') as f:
            f.write(content)
        print('File downloaded successfully.')

    image = Image.open(io.BytesIO(content))
    image.show()
    # return image 

def code_interpreter(systemprompt, file_id, query, user_name="", thread_id=None, assistant_id=None):
    """
    input: system prompt, user的file id, user的问题, user的名字(这个可加可不加)
    """

    #create assistant
    if assistant_id:
        assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
    else:
        assistant = client.beta.assistants.create(
            name="Data Analysis",
            description=systemprompt,
            model="gpt-4-1106-preview",
            tools=[{"type": "code_interpreter"}],
            file_ids=[file_id]
        )

    print(f'{assistant.id=}')
    print(f'{query=}')
    print(f'{type(query)=}')

    #create a thread：里面有user的问题和user的file id
    if thread_id:
        thread = client.beta.threads.retrieve(thread_id=thread_id)
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
    else:
        thread = client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": query,
                "file_ids": [file_id]
                }
            ]
        )

    print(f'{thread.id=}')

    #create run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=f"Please address the user as {user_name}. The user has a premium account."
    )

    print(f'{run.id=}')

    time.sleep(10)

    #retrieve the run and keep polling until it completes
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    while True:
        print(f'{run.id=} {run.status=}')

        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        status = run.status

        if status == 'in_progress':
            time.sleep(10)
        else:
            break 

    #retrieve the messages 
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

   
    return messages, thread.id, assistant.id


"""
TODO
file upload里面传入的是前端收到的file
query是前端user的问题
"""
# file_id = file_upload("AFFF_test.xlsx")
# query = "analyze this file for me"
# query = "plot the correlation for the numerical columns in the dataset."

def main():
    file_id = None
    thread_id = None
    assistant_id = None

    while True:
        if thread_id and assistant_id:
            use_existing_chat = input("Do you want to continue with the existing chat? (yes/no): ").lower()
            if use_existing_chat == 'no':
                thread_id = None  # Reset thread_id if user opts not to use existing thread
                assistant_id = None
                file_id = None
            elif use_existing_chat != 'yes' and use_existing_chat != 'no':
                continue

        if file_id:
            use_existing = input("Do you want to use the existing file? (yes/no): ").lower()
            if use_existing == 'no':
                file_id = None  # Reset file_id if user opts not to use existing file
                thread_id = None
                assistant_id = None
            elif use_existing != 'yes' and use_existing != 'no':
                continue


        if not file_id:
            file_path = input("Enter the file path or 'exit' to quit: ")
            if file_path.lower() == 'exit':
                break
        
            try:
                file_id = file_upload(file_path)
            except Exception as e:
                print('Error occurred when uploading the file: ', str(e))
                continue


        query = input("Enter your query or 'exit' to quit: ")
        if query.lower() == 'exit':
            break

        messages, thread_id, assistant_id = code_interpreter(systemprompt, file_id, query, thread_id=thread_id, assistant_id=assistant_id)

        print(messages)
        print('\n')

        # check回答的是image还是text
        if messages.data[0].content[0].type == "image_file":
            # 这个print的是api的文字respond
            print(messages.data[0].content[1].text.value)

            # 这个print的是api的图片respond
            retrieve_file(messages.data[0].content[0].image_file.file_id)

        elif messages.data[0].content[0].type == "text":
            print(f"Assistant respond: {messages.data[0].content[0].text.value}")


if __name__ == "__main__":
    main()
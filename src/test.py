import mindmap.mindmap_helper as mindmap_helper

def main():
    document = mindmap_helper.MindmapDocument(charttype="auto")
    document.get_mindmap()
    return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise e

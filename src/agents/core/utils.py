from langchain_core.runnables.graph import MermaidDrawMethod


def save_graph_as_png(graph, file_path):
    graph.get_graph(xray=1).draw_mermaid_png(
        draw_method=MermaidDrawMethod.PYPPETEER,
        output_file_path=file_path
    )
    print(f"Graph saved as '{file_path}'")

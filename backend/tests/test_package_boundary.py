from pathlib import Path

import ped_agent

import ped_agent_server


def test_core_and_server_are_distinct_python_packages() -> None:
    core_path = Path(ped_agent.__file__).resolve()
    server_path = Path(ped_agent_server.__file__).resolve()

    assert core_path != server_path
    assert core_path.parts[-2] == "ped_agent"
    assert server_path.parts[-2] == "ped_agent_server"


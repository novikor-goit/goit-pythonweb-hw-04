import argparse
import asyncio
import logging

from aiopath import AsyncPath  # type: ignore
from aioshutil import copyfile  # type: ignore
from rich.logging import RichHandler  # type: ignore


def declare_cli_interface() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="HW4",
        description="Sort files from source to destination folder and group them by extension",
    )
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


async def copy_file(source: AsyncPath, destination: AsyncPath) -> None:
    extension = source.suffix
    target_dir = destination.joinpath(extension.lstrip("."))
    await target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / source.name
    logging.debug(f"{source} -> {target_file}")

    try:
        await copyfile(source, target_file)
    except Exception as e:
        logging.error(f"Failed to copy {source} to {target_file}: {e}")


async def read_folder(source: AsyncPath, destination: AsyncPath) -> None:
    tasks = []
    async for sub_item in source.iterdir():
        if await sub_item.is_dir():
            tasks.append(read_folder(sub_item, destination))
        else:
            tasks.append(copy_file(sub_item, destination))
    await asyncio.gather(*tasks)


async def main(source: AsyncPath, destination: AsyncPath) -> None:
    logging.debug(f"Source: {source}")
    logging.debug(f"Destination: {destination}")
    if not await source.is_dir():
        logging.error(f"Source {source} is not a directory")
        return

    try:
        if not await destination.is_dir():
            await destination.mkdir(parents=True, exist_ok=True)
        await read_folder(source, destination)
    except Exception as e:
        logging.critical(e)
        raise e


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    args = declare_cli_interface().parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().handlers = [RichHandler()]

    asyncio.run(main(AsyncPath(args.source), AsyncPath(args.destination)))

    print("Done\n")

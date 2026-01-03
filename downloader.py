#!/usr/bin/env python3
"""
Script to download addons from GitHub from text with URLs.
Supports multiple input formats with GitHub URLs.
"""

import re
import os
import shutil
import stat
from pathlib import Path
from typing import Set, List
from git import Repo
from git.exc import GitCommandError


def _handle_remove_readonly(func, path, exc_info):
    """Clear read-only attribute and retry removal on Windows."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        raise


def extract_github_urls(text: str) -> Set[str]:
    """
    Extracts all GitHub URLs from text using regex.
    
    Supports formats like:
    - https://github.com/user/repo
    - https://github.com/user/repo.git
    - URLs in lines with other data
    
    Args:
        text: Text to parse
        
    Returns:
        Set of unique GitHub URLs
    """
    # Regex to capture GitHub URLs
    github_pattern = r'https?://github\.com/[^\s/]+/[^\s)"\']+(?:\.git)?(?=\s|$|[\)\"\'])'
    
    urls = set(re.findall(github_pattern, text, re.IGNORECASE))
    
    return urls


def extract_repo_name(url: str) -> str:
    """
    Extracts the repository name from the URL.
    
    Args:
        url: Repository URL
        
    Returns:
        Repository name without .git
    """
    # Remove .git from the end if it exists
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # Get the last part of the path
    repo_name = url.split('/')[-1]
    return repo_name


def clone_repository(url: str, dest_path: Path) -> bool:
    """
    Clones a GitHub repository.
    
    Args:
        url: Repository URL
        dest_path: Destination path for cloning
        
    Returns:
        True if successful, False otherwise
    """
    repo_name = extract_repo_name(url)
    repo_path = dest_path / repo_name
    
    try:
        # If folder already exists, remove it
        if repo_path.exists():
            print(f"  ⚠️  Existing folder: {repo_name} - replacing...")
            shutil.rmtree(repo_path)
        
        print(f"  ⏳ Downloading: {repo_name}...", end=" ", flush=True)
        Repo.clone_from(url, str(repo_path))
        print("✅")
        return True
        
    except GitCommandError as e:
        print(f"❌ Error cloning {repo_name}")
        print(f"     Details: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error with {repo_name}: {str(e)}")
        return False


def main():
    """Main script function."""
    
    print("=" * 60)
    print("📦 GitHub Addon Downloader")
    print("=" * 60)
    print()
    
    # Get input text
    print("Paste the text with GitHub URLs (finish with an empty line):")
    print("(Press Enter twice when done)")
    print("-" * 60)
    
    lines = []
    try:
        while True:
            line = input()
            if line == "":
                if lines and lines[-1] == "":
                    lines.pop()  # Remove last empty line
                    break
            lines.append(line)
    except EOFError:
        pass  # End of input
    
    text_input = "\n".join(lines)
    
    if not text_input.strip():
        print("❌ No text entered. Aborting.")
        return
    
    print()
    
    # Extract URLs
    urls = extract_github_urls(text_input)
    
    if not urls:
        print("❌ No GitHub URLs found in the text.")
        return
    
    print(f"✅ Found {len(urls)} repository(ies):")
    for url in sorted(urls):
        print(f"   • {url}")
    print()
    
    # Define destination folder
    data_path = Path("./AddOns").resolve()
    
    # Check if folder exists
    if data_path.exists():
        print(f"📁 Folder '{data_path}' already exists.")
        print()
        print("What would you like to do?")
        print("  1. Delete folder and download again (replace all)")
        print("  2. Add/update addons (keep existing)")
        print()
        
        while True:
            choice = input("Select an option (1 or 2): ").strip()
            if choice in ["1", "2"]:
                break
            print("❌ Invalid option. Enter 1 or 2.")
        
        print()
        
        if choice == "1":
            print(f"🗑️  Deleting folder {data_path}...")
            try:
                shutil.rmtree(data_path, onerror=_handle_remove_readonly)
                data_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"❌ Could not delete or recreate folder. Details: {e}")
                print("👉 Close any program using files inside AddOns (e.g., Explorer, editors, Git).")
                return
        else:
            try:
                data_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"❌ Could not create folder. Details: {e}")
                return
    else:
        print(f"📁 Creating folder: {data_path}")
        try:
            data_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Could not create folder. Details: {e}")
            return
    
    print()
    print("=" * 60)
    print("⬇️  Starting repository downloads...")
    print("=" * 60)
    print()
    
    # Download repositories
    successful = 0
    failed = 0
    failed_repos = []
    
    for i, url in enumerate(sorted(urls), 1):
        print(f"[{i}/{len(urls)}]", end=" ")
        if clone_repository(url, data_path):
            successful += 1
        else:
            failed += 1
            failed_repos.append(url)
    
    print()
    print("=" * 60)
    print("📊 Download Summary")
    print("=" * 60)
    print(f"✅ Successful:  {successful}")
    print(f"❌ Failed:  {failed}")
    
    if failed_repos:
        print()
        print("Repositories with errors:")
        for url in failed_repos:
            print(f"  • {url}")
    
    print()
    print(f"✅ Repositories downloaded to: {data_path}")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_document import File, History, User

def migrate_files_to_owner_ids():
    """Migrate files to have owner IDs based on associated history documents"""
    print("Starting file migration...")
    
    # Get all files
    files = File.objects()
    total = files.count()
    migrated = 0
    skipped = 0
    failed = 0
    
    print(f"Found {total} files to process")
    
    for file in files:
        try:
            # Skip if already migrated
            if hasattr(file, 'owner_id') and file.owner_id:
                print(f"Skipping already migrated file: {file.id}")
                skipped += 1
                continue
            
            # Try to find owner through history documents
            history = History.objects(file_ids=str(file.id)).first()
            if history and hasattr(history, 'user_id') and history.user_id:
                file.owner_id = history.user_id
                file.save()
                print(f"Successfully migrated file {file.id} to owner {history.user_id}")
                migrated += 1
                continue
            
            # If no history found, try to find through document_id
            if hasattr(file, 'document_id') and file.document_id:
                history = History.objects(id=file.document_id).first()
                if history and hasattr(history, 'user_id') and history.user_id:
                    file.owner_id = history.user_id
                    file.save()
                    print(f"Successfully migrated file {file.id} to owner {history.user_id} through document_id")
                    migrated += 1
                    continue
            
            # If still no owner found, assign to first admin user
            admin = User.objects(role='admin').first()
            if admin:
                file.owner_id = str(admin.id)
                file.save()
                print(f"Assigned file {file.id} to admin user {admin.email}")
                migrated += 1
            else:
                print(f"Could not find an owner for file {file.id}, skipping")
                skipped += 1
            
        except Exception as e:
            print(f"Error migrating file {file.id}: {str(e)}")
            failed += 1
            continue
    
    print("\nMigration complete!")
    print(f"Total files processed: {total}")
    print(f"Successfully migrated: {migrated}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

if __name__ == '__main__':
    migrate_files_to_owner_ids() 
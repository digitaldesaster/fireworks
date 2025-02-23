#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_document import History, User

def migrate_history_to_user_ids():
    """Migrate history documents to use user IDs instead of usernames"""
    print("Starting history migration...")
    
    # Get all history documents
    histories = History.objects()
    total = histories.count()
    migrated = 0
    skipped = 0
    failed = 0
    
    print(f"Found {total} history documents to process")
    
    for history in histories:
        try:
            # Skip if already migrated
            if hasattr(history, 'user_id') and history.user_id:
                print(f"Skipping already migrated history: {history.id}")
                skipped += 1
                continue
                
            # Find user by email
            if not hasattr(history, 'username') or not history.username:
                print(f"Skipping history without username: {history.id}")
                skipped += 1
                continue
                
            user = User.objects(email=history.username).first()
            if not user:
                print(f"Could not find user for email {history.username}, skipping history: {history.id}")
                skipped += 1
                continue
            
            # Update history document
            history.user_id = str(user.id)
            history.save()
            print(f"Successfully migrated history {history.id} for user {user.email}")
            migrated += 1
            
        except Exception as e:
            print(f"Error migrating history {history.id}: {str(e)}")
            failed += 1
            continue
    
    print("\nMigration complete!")
    print(f"Total documents processed: {total}")
    print(f"Successfully migrated: {migrated}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

if __name__ == '__main__':
    migrate_history_to_user_ids() 
package org.springframework.boot.loader;

import org.springframework.boot.loader.archive.Archive;

public class WarLauncher extends ExecutableArchiveLauncher {
   public WarLauncher() {
   }

   protected WarLauncher(Archive archive) {
      super(archive);
   }

   @Override
   protected boolean isPostProcessingClassPathArchives() {
      return false;
   }

   @Override
   protected boolean isSearchCandidate(Archive.Entry entry) {
      return entry.getName().startsWith("WEB-INF/");
   }

   @Override
   public boolean isNestedArchive(Archive.Entry entry) {
      return entry.isDirectory()
         ? entry.getName().equals("WEB-INF/classes/")
         : entry.getName().startsWith("WEB-INF/lib/") || entry.getName().startsWith("WEB-INF/lib-provided/");
   }

   public static void main(String[] args) throws Exception {
      new WarLauncher().launch(args);
   }
}

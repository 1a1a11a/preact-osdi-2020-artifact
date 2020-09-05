package pasalab.dfs.perf.benchmark.simplewrite;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import pasalab.dfs.perf.basic.PerfThread;
import pasalab.dfs.perf.basic.TaskConfiguration;
import pasalab.dfs.perf.benchmark.ListGenerator;
import pasalab.dfs.perf.benchmark.Operators;
import pasalab.dfs.perf.conf.PerfConf;
import pasalab.dfs.perf.fs.PerfFileSystem;

public class SimpleWriteThread extends PerfThread {
  private int mBufferSize;
  private long mFileLength;
  private PerfFileSystem mFileSystem;
  private List<String> mWriteFiles;
  private List<Long> mLatency;

  private boolean mSuccess;
  private double mThroughput; // in MB/s

  public boolean getSuccess() {
    return mSuccess;
  }

  public double getThroughput() {
    return mThroughput;
  }

  public List<Long> getLatency() {
    return mLatency;
  }

  public void clearHistory() {
    mThroughput = 0.0;
    mLatency = new ArrayList<Long>();
  }

  public void run() {
    long writeBytes = 0;
    mSuccess = true;
    LOG.trace("Write total " + mWriteFiles.size() + " files.");
    clearHistory();
    long timeMs = System.currentTimeMillis();
    for (String fileName : mWriteFiles) {
      long startTime = System.currentTimeMillis();
      try {
        LOG.trace("Write file " + fileName + " with size " + mFileLength);
        Operators.writeSingleFile(mFileSystem, fileName, mFileLength, mBufferSize,
            "SimpleWrite", mTaskId, mId);
        writeBytes += mFileLength;
      } catch (IOException e) {
        LOG.error("Failed to write file " + fileName, e);
        mSuccess = false;
      }
      long endTime = System.currentTimeMillis();
      long duration = endTime - startTime;
      mLatency.add(duration);
      LOG.info("HeART-DFS-PERF-Metrics-SimpleWrite-FILE || " + mTaskId + "," + mId + ","
          + startTime + "," + endTime + "," + duration + ","
          + mFileLength + "," + ((mFileLength / 1024.0 / 1024.0) / (duration / 1000.0)) + " ||");
    }
    timeMs = System.currentTimeMillis() - timeMs;
    mThroughput = (writeBytes / 1024.0 / 1024.0) / (timeMs / 1000.0);
  }

  @Override
  public boolean setupThread(TaskConfiguration taskConf) {
    mBufferSize = taskConf.getIntProperty("buffer.size.bytes");
    mFileLength = taskConf.getLongProperty("file.length.bytes");
    try {
      mFileSystem = Operators.connect(PerfConf.get().DFS_ADDRESS, taskConf);
      String writeDir = taskConf.getProperty("write.dir");
      int filesNum = taskConf.getIntProperty("files.per.thread");
      mWriteFiles = ListGenerator.generateWriteFiles(mId, filesNum, writeDir);
    } catch (IOException e) {
      LOG.error("Failed to setup thread, task " + mTaskId + " - thread " + mId, e);
      return false;
    }
    mSuccess = false;
    mThroughput = 0;
    mLatency = new ArrayList<Long>();
    return true;
  }

  @Override
  public boolean cleanupThread(TaskConfiguration taskConf, boolean closeFileSystem) {
    try {
      if (closeFileSystem) Operators.close(mFileSystem);
    } catch (IOException e) {
      LOG.warn("Error when close file system, task " + mTaskId + " - thread " + mId, e);
    }
    return true;
  }

}

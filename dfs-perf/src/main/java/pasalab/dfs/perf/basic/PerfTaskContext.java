package pasalab.dfs.perf.basic;

import java.io.File;
import java.io.IOException;

import org.apache.log4j.Logger;

import pasalab.dfs.perf.PerfConstants;

/**
 * The abstract class for all test statistics. For new test, you should implement your own
 * PerfTaskContext.
 */
public abstract class PerfTaskContext {
  protected static final Logger LOG = Logger.getLogger(PerfConstants.PERF_LOGGER_TYPE);

  protected int mId;
  protected int mIteration;
  protected String mNodeName;
  protected String mTestCase;

  protected long mFinishTimeMs;
  protected long mStartTimeMs;
  protected boolean mSuccess;

  public void initial(int id, String nodeName, String testCase, TaskConfiguration taskConf) {
    mId = id;
    mIteration = 0;
    mNodeName = nodeName;
    mTestCase = testCase;
    mStartTimeMs = System.currentTimeMillis();
    mFinishTimeMs = mStartTimeMs;
    mSuccess = true;
  }

  public int getId() {
    return mId;
  }

  public int getIteration() { return mIteration; }

  public void setIteration(int currentIteration) { mIteration = currentIteration; }

  public String getNodeName() {
    return mNodeName;
  }

  public String getTestCase() {
    return mTestCase;
  }

  public long getFinishTimeMs() {
    return mFinishTimeMs;
  }

  public long getStartTimeMs() {
    return mStartTimeMs;
  }

  public boolean getSuccess() {
    return mSuccess;
  }

  public void setStartTimeMs(long startTimeMs) {
    mStartTimeMs = startTimeMs;
  }

  public void setFinishTimeMs(long finishTimeMs) {
    mFinishTimeMs = finishTimeMs;
  }

  public void setSuccess(boolean success) {
    mSuccess = success;
  }

  /**
   * Load this task context from file
   * 
   * @param file the input file
   * @throws IOException
   */
  public abstract void loadFromFile(File file) throws IOException;

  /**
   * Set contexts from test threads.
   * 
   * @param threads
   */
  public abstract void setFromThread(PerfThread[] threads);

  /**
   * Output this task context to file.
   * 
   * @param file the output file
   * @throws IOException
   */
  public abstract void writeToFile(File file) throws IOException;
}

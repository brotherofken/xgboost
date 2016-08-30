/*!
 * Copyright (c) 2015 by Contributors
 * \file logging.h
 * \brief defines console logging options for xgboost.
 *  Use to enforce unified print behavior.
 *  For debug loggers, use LOG(INFO) and LOG(ERROR).
 */
#ifndef XGBOOST_LOGGING_H_
#define XGBOOST_LOGGING_H_

#include <dmlc/logging.h>
#include <sstream>
#include "./base.h"

namespace xgboost {

class BaseLogger {
 public:
  BaseLogger() {
#if XGBOOST_LOG_WITH_TIME
    log_stream_ << "[" << dmlc::DateLogger().HumanDate() << "] ";
#endif
  }
  std::ostream& stream() { return log_stream_; }

 protected:
  std::ostringstream log_stream_;
};

class ConsoleLogger : public BaseLogger {
 public:
  ~ConsoleLogger();
};

class TrackerLogger : public BaseLogger {
 public:
  ~TrackerLogger();
};

// redefines the logging macro if not existed
#ifndef LOG
#define LOG(severity) LOG_##severity.stream()
#endif

//#define ODS_LOG_ENABLED
#ifdef ODS_LOG_ENABLED
#define ODS_LOG(X) std::cerr << X << std::endl;
#define ODS_LOGNLF(X) std::cerr << X;
#else
#define ODS_LOG(X)
#define ODS_LOGNLF(X)
#endif

// Enable LOG(CONSOLE) for print messages to console.
#define LOG_CONSOLE ::xgboost::ConsoleLogger()
// Enable LOG(TRACKER) for print messages to tracker
#define LOG_TRACKER ::xgboost::TrackerLogger()
}  // namespace xgboost.
#endif  // XGBOOST_LOGGING_H_

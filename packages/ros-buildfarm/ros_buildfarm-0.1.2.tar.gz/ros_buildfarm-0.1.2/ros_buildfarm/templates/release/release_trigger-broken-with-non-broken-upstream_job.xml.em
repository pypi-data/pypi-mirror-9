<project>
  <actions/>
  <description>Generated at @ESCAPE(now_str) from template '@ESCAPE(template_name)'</description>
@(SNIPPET(
    'log-rotator',
    days_to_keep=365,
    num_to_keep=30,
))@
  <keepDependencies>false</keepDependencies>
  <properties>
@(SNIPPET(
    'property_job-priority',
    priority=40,
))@
@(SNIPPET(
    'property_requeue-job',
))@
@(SNIPPET(
    'property_disk-usage',
))@
  </properties>
@(SNIPPET(
    'scm_null',
))@
  <assignedNode>master</assignedNode>
  <canRoam>false</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
@(SNIPPET(
    'trigger_timer',
    spec='1 23 * * *',
))@
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
@(SNIPPET(
    'builder_system-groovy',
    command=
"""import java.util.regex.Matcher
import java.util.regex.Pattern

import hudson.model.Cause
import hudson.model.Result

println "Triggering builds for the following jobs:"

def source_prefix = "%s"
def binary_prefix = "%s"
pattern_src = Pattern.compile(source_prefix + "__.+__.+__source")
pattern_bin = Pattern.compile(binary_prefix + "__.+__.+__binary")
for (p in hudson.model.Hudson.instance.projects) {
    if (!pattern_src.matcher(p.name).matches() && !pattern_bin.matcher(p.name).matches()) continue
    if (p.isDisabled()) continue
    if (p.isInQueue() || p.isBuilding()) continue

    // skip (un)stable jobs
    if (p.getNextBuildNumber() > 1) {
        def lb = p.getLastBuild()
        if (lb) {
            def r = lb.getResult()
            if (r) {
                if (r.isBetterOrEqualTo(Result.UNSTABLE)) continue
            }
        }
    }

    // skip if any upstream job is broken
    any_upstream_broken = false
    for (u in p.getUpstreamProjects()) {
        any_upstream_broken = true
        if (u.getNextBuildNumber() > 1) {
            def lb = u.getLastBuild()
            if (lb) {
                def r = lb.getResult()
                if (r) {
                    if (r.isBetterOrEqualTo(Result.UNSTABLE)) {
                        any_upstream_broken = false
                    }
                }
            }
        }
        if (any_upstream_broken) break
    }
    if (any_upstream_broken) continue

    println p.name

    scheduled = p.scheduleBuild(new Cause.UserIdCause())
    if (!scheduled) {
        println "  FAILED to schedule build"
    }
}
""" % (source_project_name_prefix, binary_project_name_prefix),
    script_file=None,
    classpath='',
))@
  </builders>
  <publishers>
@(SNIPPET(
    'publisher_mailer',
    recipients=recipients,
    dynamic_recipients=[],
    send_to_individuals=False,
))@
  </publishers>
  <buildWrappers>
@(SNIPPET(
    'build-wrapper_timestamper',
))@
@(SNIPPET(
    'build-wrapper_disk-check',
))@
  </buildWrappers>
</project>

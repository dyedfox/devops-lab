import boto3
import logging
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError
import time

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# https://docs.aws.amazon.com/code-library/latest/ug/python_3_cloudwatch_code_examples.html
class CloudWatchWrapper:
    """Encapsulates Amazon CloudWatch functions."""

    def __init__(self, cloudwatch_resource):
        """
        :param cloudwatch_resource: A Boto3 CloudWatch resource.
        """
        self.cloudwatch_resource = cloudwatch_resource

    def get_metric_statistics(
        self, namespace, name, start, end, period, stat_types, dimensions=None
    ):
        """
        Gets statistics for a metric within a specified time span. Metrics are grouped
        into the specified period.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param start: The UTC start time of the time span to retrieve.
        :param end: The UTC end time of the time span to retrieve.
        :param period: The period, in seconds, in which to group metrics.
        :param stat_types: List of statistics to retrieve, such as ['Average'].
        :param dimensions: List of dimensions to filter by (e.g., InstanceId).
        :return: The retrieved statistics for the metric.
        """
        try:
            metric = self.cloudwatch_resource.Metric(namespace, name)
            stats = metric.get_statistics(
                StartTime=start,
                EndTime=end,
                Period=period,
                Statistics=stat_types,
                Dimensions=dimensions or [],
            )
            logger.info(
                "Got %s statistics for %s.", len(stats["Datapoints"]), stats["Label"]
            )
        except ClientError:
            logger.exception("Couldn't get statistics for %s.%s.", namespace, name)
            raise
        else:
            return stats


def main():
    # AWS setup
    region = "us-west-2"
    cloudwatch = boto3.resource("cloudwatch", region_name=region)

    # Initialize wrapper
    cw_wrapper = CloudWatchWrapper(cloudwatch)

    # Metric details

    namespace = "CWAgent"
    metric_name = "mem_used_percent"
    instance_id = "i-03e5a4b5d30a614e4"
    dimensions = [{"Name": "InstanceId", "Value": instance_id}]

    # namespace = "AWS/EC2"
    # metric_name = "CPUUtilization"
    # image_id = "ami-055495e6fc65e4321"
    # dimensions = [{"Name": "ImageId", "Value": image_id}]

    # Time range: last 1 hour
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)


    # Statistic details
    period = 60
    stat_types = ["Average"]

    # Get and print metric statistics

    for i in range(15):
        try:
            stats = cw_wrapper.get_metric_statistics(
                namespace=namespace,
                name=metric_name,
                start=start_time,
                end=end_time,
                period=period,
                stat_types=stat_types,
                dimensions=dimensions,
            )
            print(f"Iteration {i + 1}: Metric statistics:")
            for dp in sorted(stats["Datapoints"], key=lambda x: x["Timestamp"]):
                print(f"Time: {dp['Timestamp']}, Average: {dp['Average']:.2f}%")
        except Exception as e:
            print(f"Failed to retrieve metric data: {e}")
        # Sleep for 5 minutes before the next request
        print("Sleeping for 1 minute...")
        time.sleep(60)

    # while True:
    #     try:
    #         stats = cw_wrapper.get_metric_statistics(
    #             namespace=namespace,
    #             name=metric_name,
    #             start=start_time,
    #             end=end_time,
    #             period=period,
    #             stat_types=stat_types,
    #             dimensions=dimensions,
    #         )
    #         print("Metric statistics:")
    #         for dp in sorted(stats["Datapoints"], key=lambda x: x["Timestamp"]):
    #             print(f"Time: {dp['Timestamp']}, Average: {dp['Average']:.2f}%")
    #     except Exception as e:
    #         print(f"Failed to retrieve metric data: {e}")
    #     # Sleep for 5 minutes before the next request
    #     print("Sleeping for 5 minutes...")
    #     time.sleep(300)

if __name__ == "__main__":
    main()
package pbi.executor;

import pbi.executor.types.*;

public final class Timsort {
  static int RUN = 32;

  // this function sorts array from left index to
  // to right index which is of size atmost THREASHOLD

  public static void insertionSort(Base[] arr, Base key_m, int left, int right) throws Throwable {
    for (int i = left + 1; i <= right; i++) {
      Base temp = arr[i];
      Base temp_k = key_m == null ? temp : key_m.__call__(temp);
      int j = i - 1;
      while (j >= 0 && (key_m == null ? arr[j] : key_m.__call__(arr[j])).__gt(temp_k).__bool() && j >= left) {
        arr[j + 1] = arr[j];
        j--;
      }
      arr[j + 1] = temp;
    }
  }

  public static void insertionSortReverse(Base[] arr, Base key_m, int left, int right) throws Throwable {
    for (int i = left + 1; i <= right; i++) {
      Base temp = arr[i];
      Base temp_k = key_m == null ? temp : key_m.__call__(temp);
      int j = i - 1;
      while (j >= 0 && (key_m == null ? arr[j] : key_m.__call__(arr[j])).__lt(temp_k).__bool() && j >= left) {
        arr[j + 1] = arr[j];
        j--;
      }
      arr[j + 1] = temp;
    }
  }

  // merge function merges the sorted runs
  public static void merge(Base[] arr, Base key, boolean reverse, int left, int mid, int right) throws Throwable {
    //System.out.println("tim: " + left + " " + mid + " " + right);
    int leftArryLen = mid - left + 1, rightArrLen = right - mid;
    if (rightArrLen < 1) return;
    Base[] leftArr = new Base[leftArryLen];
    Base[] rightArr = new Base[rightArrLen];

    for (int x = 0; x < leftArryLen; x++) {
      leftArr[x] = arr[left + x];
    }

    for (int x = 0; x < rightArrLen; x++) {
      rightArr[x] = arr[mid + 1 + x];
    }

    int i = 0, j = 0, k = left;
    if (key == null) {
      if (reverse) {
        while (i < leftArryLen && j < rightArrLen) {
          Base a = leftArr[i], b = rightArr[j];
          if (b.__lt(a).__bool()) {
            arr[k++] = a;
            i++;
          } else {
            arr[k++] = b;
            j++;
          }
        }
      } else {
        while (i < leftArryLen && j < rightArrLen) {
          Base a = leftArr[i], b = rightArr[j];
          if (b.__gt(a).__bool()) {
            arr[k++] = a;
            i++;
          } else {
            arr[k++] = b;
            j++;
          }
        }
      }
    } else {
      if (reverse) {
        while (i < leftArryLen && j < rightArrLen) {
          Base a = leftArr[i], b = rightArr[j];
          if (key.__call__(b).__lt(key.__call__(a)).__bool()) {
            arr[k++] = a;
            i++;
          } else {
            arr[k++] = b;
            j++;
          }
        }
      } else {
        while (i < leftArryLen && j < rightArrLen) {
          Base a = leftArr[i], b = rightArr[j];
          if (key.__call__(b).__gt(key.__call__(a)).__bool()) {
            arr[k++] = a;
            i++;
          } else {
            arr[k++] = b;
            j++;
          }
        }
      }
    }
    while (i < leftArryLen) arr[k++] = leftArr[i++];
    while (j < rightArrLen) arr[k++] = rightArr[j++];
  }

  public static void timSort(Base[] arr, Base key, boolean reverse) throws Throwable {
    int length = arr.length;

    // Sort individual subarrays of size THRESHOLD
    if (reverse)
      for (int i = 0; i < length; i += RUN)
        // perform insertion sort
        insertionSortReverse(arr, key, i, Math.min(i + 32, length) - 1);
    else
      for (int i = 0; i < length; i += RUN)
        // perform insertion sort
        insertionSort(arr, key, i, Math.min(i + 32, length) - 1);

    for (int size = RUN; size < length; size = 2 * size) {
      for (int left = 0; left < length; left += 2 * size) {
        int mid = left + size - 1;
        int right = Math.min(left + 2 * size, length) - 1;
        // perform merge sort
        merge(arr, key, reverse, left, mid, right);
      }
    }
  }

  /*class Test extends Base {
    @Override public Base __call__(Base... obj) throws Throwable {
      long num = obj[0].__num();
      return new BigInt(-num);
    }
  }

  public static void main(String[] args) {
    Random r = new Random();
    int len = 100;
    Base[] arr = new Base[len];
    for (int i = 0; i < len; i++) arr[i] = new BigInt(r.nextInt(100));
    
    Main.printObj("arr: ", arr);
    try {
      timSort(arr, null); // new Timsort().new Test());
    } catch (Throwable e) {
      e.printStackTrace();
    }
    Main.printObj("arr: ", arr);
  }*/
}